# Using these pry gems
# gem "pry"
# gem "pry-rails"
# gem "pry-doc"

# Fix for Zeus: see https://github.com/burke/zeus/issues/466#issuecomment-60242431
if defined?(::Rails) && Rails.env
  if Rails::VERSION::MAJOR == 3
    verbose, $VERBOSE = $VERBOSE, nil
    if defined?(Rails::Console)
      Rails::Console::IRB = ::Pry unless Rails::Console::IRB == ::Pry
    end
    $VERBOSE = verbose

    unless defined? ::Pry::ExtendCommandBundle
      ::Pry::ExtendCommandBundle = Module.new
    end
  end

  if defined?(Rails) && Rails::VERSION::MAJOR == 4 && Rails.application
    unless Rails.application.config.console == ::Pry
      Rails.application.config.console = ::Pry
    end
  end

  if ((Rails::VERSION::MAJOR == 3 && Rails::VERSION::MINOR >= 2) ||
      Rails::VERSION::MAJOR == 4)
    unless defined? ::Rails::ConsoleMethods
      require 'rails/console/app'
      require 'rails/console/helpers'

      TOPLEVEL_BINDING.eval('self').extend ::Rails::ConsoleMethods
    end
  end
end

# #### END FIX FOR ZEUS

Pry::Commands.block_command "noconflict", "Rename step to sstep and next to nnext" do
  Pry::Commands.rename_command("nnext", "next")
  Pry::Commands.rename_command("bbreak", "break")
end

Pry::Commands.block_command "unnoconflict", "Revert to normal next and break" do
  Pry::Commands.rename_command("next", "nnext")
  Pry::Commands.rename_command("break", "bbreak")
end

Pry.config.color = true
Pry.config.prompt = Pry::NAV_PROMPT

begin
  require 'awesome_print'
  # Pry.config.print = proc { |output, value| output.puts value.ai }
  AwesomePrint.pry!
rescue LoadError => err
  puts "no awesome_print :("
end

my_hook = Pry::Hooks.new.add_hook(:before_session, :add_dirs_to_load_path) do
  # adds the directories /spec and /test directories to the path if they exist and not already included
  dir = `pwd`.chomp
  dirs_added = []
  %w(spec test presenters lib).map{ |d| "#{dir}/#{d}" }.each do |p|
    if File.exist?(p) && !$:.include?(p)
      $: << p
      dirs_added << p
    end
  end
  puts "Added #{ dirs_added.join(", ") } to load path in ~/.pryrc." if dirs_added.present?
end

my_hook.exec_hook(:before_session)
