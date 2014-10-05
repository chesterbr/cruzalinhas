namespace :geohashes do
  desc "Recalculates the hashes for the first trip of each route"
  task rehash: :environment do
    TripGeohash.delete_all
    GtfsEngine::Route.all.each do |route|
      next if route.trips.empty?
      puts "#{route.route_short_name} #{route.route_long_name}"
      trip = route.trips.first
      geohashes = trip.shapes.map { |shape|
        GeoHash.encode shape.shape_pt_lat,
                       shape.shape_pt_lon,
                       Rails.configuration.geohash_precision
      }.uniq
      geohashes.each do |geohash|
        TripGeohash.create(:trip => trip, :geohash => geohash)
      end
    end
  end
end
