source 'https://rubygems.org'


# Bundle edge Rails instead: gem 'rails', github: 'rails/rails'
gem 'rails', '~> 7.2.2'
# Use sqlite3 as the database for Active Record
gem 'sqlite3'
# Use SCSS for stylesheets
gem 'sass-rails'
# Use Uglifier as compressor for JavaScript assets
gem 'uglifier', '>= 1.3.0'
# Use CoffeeScript for .js.coffee assets and views
gem 'coffee-rails'
# See https://github.com/sstephenson/execjs#readme for more supported runtimes
# gem 'therubyracer',  platforms: :ruby

# Use jquery as the JavaScript library
gem 'jquery-rails'
# Turbolinks makes following links in your web application faster. Read more: https://github.com/rails/turbolinks
gem 'turbolinks'
# Build JSON APIs with ease. Read more: https://github.com/rails/jbuilder
gem 'jbuilder', '~> 2.0'
# bundle exec rake doc:rails generates the API under doc/api.
# gem 'sdoc',          group: :doc

# Spring speeds up development by keeping your application running in the background. Read more: https://github.com/rails/spring
gem 'spring',        group: :development

# This is needed because `respond_to` was dropped in Rails 4.2, and
# gtfs_engine uses it somewhere. See https://stackoverflow.com/a/40581849/64635
gem 'responders'

# Rails eagerly loads these on prod
gem 'net-smtp'
gem 'net-pop'
gem 'net-imap'

# For the /version route
gem 'git'

# Use ActiveModel has_secure_password
# gem 'bcrypt', '~> 3.1.7'

# Use unicorn as the app server
# gem 'unicorn

# Use Capistrano for deployment
# gem 'capistrano-rails', group: :development

# Use debugger
# gem 'debugger', group: [:development, :test]

group :development, :test do
  gem 'rspec-rails'
  gem 'guard-rspec', require: false
  gem 'byebug', require: false
end

group :development do
  gem 'capistrano',         require: false
  gem 'capistrano-rbenv',   require: false
  gem 'capistrano-rails',   require: false
  gem 'capistrano-bundler', require: false
  gem 'capistrano3-puma',   require: false
  gem 'capistrano-pending', require: false
end

group :production do
  gem 'puma'
end

# Remove line above when upcoming PR is merged
gem 'gtfs_reader', :github => 'chesterbr/gtfs_reader', :branch => 'activesupport-7'
# Revert line above to "gem 'gtfs_engine', '~> 2.1'" (replace 2.1 with current-ish version) when upcoming PR is merged
gem 'gtfs_engine', :github => 'chesterbr/gtfs_engine', :branch => 'rails-7'
gem 'pr_geohash', '~> 1.0.0'
