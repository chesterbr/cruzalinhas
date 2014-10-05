namespace :sptrans do
  desc 'Imports data downloaded from http://www.sptrans.com.br/desenvolvedores/ (renamed gtfs-sptrans.zip)'
  task :import do
    Rake::Task["gtfs_engine:update"].invoke
    Rake::Task["geohashes:rehash"].invoke
  end
end
