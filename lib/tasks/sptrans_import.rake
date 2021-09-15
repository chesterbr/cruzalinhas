namespace :sptrans do
  desc 'Imports data downloaded from SPTrans'
  task :import => :environment do
    puts "### STEP 1 OF 2 - Importing GTFS data from OpenMobilityData"
    FileUtils.mkdir_p "tmp/cache"
    next unless system("echo 'Downloading...'; wget https://openmobilitydata.org/p/sptrans/1049/latest/download -O/tmp/gtfs-sptrans.zip")
    Rake::Task["db:reset"].invoke
    Rake::Task["gtfs_engine:update"].invoke
    Rake::Task["geohashes:rehash"].invoke
    File.delete("/tmp/gtfs-sptrans.zip")

    puts "### STEP 2 OF 2 - Building route URLs from SPTrans website"
    uri = URI.parse("https://itinerariosapi.sptrans.com.br/RetornarLinhas")
    request = Net::HTTP::Post.new(uri)
    request["Origin"] = "https://sptrans.com.br"
    req_options = {
      use_ssl: uri.scheme == "https",
    }
    response = Net::HTTP.start(uri.hostname, uri.port, req_options) do |http|
      http.request(request)
    end
    JSON.parse(response.body).each do |linha|
      letreiro = linha["letreiro"].split(" ")
      if letreiro[0].in? %w(CPTM METRÔ)
        sigla = letreiro[0..1].join(" ").chomp("-0")
      else
        sigla = letreiro[0]
      end
      url = "https://sptrans.com.br/itinerarios/linha/?cdp=#{ linha["CdPjOID"] }"
      puts "#{linha} => #{sigla} / #{url}"
      SptransUrl.create(
        sigla: sigla,
        url: url
      )
    end
  end
end
