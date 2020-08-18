namespace :sptrans do
  desc 'Imports data downloaded from SPTrans'
  task :import do
    FileUtils.mkdir_p "tmp/cache"
    next unless system("echo 'Downloading...'; wget https://openmobilitydata.org/p/sptrans/1049/latest/download -O/tmp/gtfs-sptrans.zip")

    Rake::Task["db:reset"].invoke
    Rake::Task["gtfs_engine:update"].invoke
    Rake::Task["geohashes:rehash"].invoke

    File.delete("/tmp/gtfs-sptrans.zip")
  end
end
