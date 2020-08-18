namespace :sptrans do
  desc 'Imports data downloaded from SPTrans'
  task :import do
    unless ENV["GTFS_SPTRANS_ZIP_FILE"]
      puts <<~INSTRUCTIONS
        This task requires a zip file with the SPTrans itinerary information.
        You can download it here: https://openmobilitydata.org/p/sptrans/1049/latest/download

        Once downloaded, set GTFS_SPTRANS_ZIP_FILE with file to import. E.g.:

        GTFS_SPTRANS_ZIP_FILE=/tmp/gtfs-sptrans.zip bin/rake sptrans:import
      INSTRUCTIONS
      next
    end
    Rake::Task["db:reset"].invoke
    Rake::Task["gtfs_engine:update"].invoke
    Rake::Task["geohashes:rehash"].invoke
  end
end
