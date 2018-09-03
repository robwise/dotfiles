alias fsp="bundle exec foreman start -f Procfile.dev"
alias fss="bundle exec foreman start -f Procfile.spec"
alias sb="bundle exec spring rails console --sandbox"
alias binstub="bundle exec spring binstub --all"
alias beg="bundle exec guard --clear"
alias ber="bundle exec rake"
alias ut="rspec --tag ~type:feature --tag ~slow --tag ~js --exclude-pattern '**/requests/*_spec.rb, **/features/*_spec.rb'"

# This allows the use of [] without escapes
alias rake='noglob rake'

alias redomigration="rails db:rollback && rails db:migrate && rails db:rollback RAILS_ENV=test && rails db:migrate RAILS_ENV=test"
alias migrate="rails db:migrate && RAILS_ENV=test rails db:migrate"
alias rollback="rails db:rollback && RAILS_ENV=test rails db:migrate"
alias resettestdb="RAILS_ENV=test rails db:reset"

export PROCESSES_TO_QUIT='puma rake sidekiq spring rails$ ruby-debug phantomjs zeus passenger guard resque "node server.js" ruby$ node foreman'

pgr() {
    echo "Finding processes in list: $PROCESSES_TO_QUIT"
    echo $PROCESSES_TO_QUIT | xargs -n 1 pgrep -l
}

pgk() {
    echo "Killing processes in list: $PROCESSES_TO_QUIT"
    echo $PROCESSES_TO_QUIT | xargs -n 1 pkill -l
}

pgkk() {
    echo "Killing -9 processes in list: $PROCESSES_TO_QUIT"
    echo "Also removing $ZEUS_SOCK if existing"
    echo $PROCESSES_TO_QUIT | xargs -n 1 pkill -9 -l
}

rspec-say() {
    rspec $@
    say "r spec test completed"
}
