class PythonApiController < ApplicationController
  def linhasquepassam
    geohash = GeoHash.encode params[:lat].to_f,
                             params[:lng].to_f,
                             Rails.configuration.geohash_precision
    trips = TripGeohash.includes(:trip, :trip => :route).where(:geohash => geohash).map { |h|
      {
        url: "http://www.toape.com.br/#{h.trip.route.route_short_name}/",
        hashes: TripGeohash.where(trip: h.trip).pluck(:geohash),
        key: h.trip_id,
        nome: "#{h.trip.route.route_short_name}: #{h.trip.route.route_long_name}"
      }
    }

    render json: trips
  end

  def linha
    trip   = GtfsEngine::Trip.find(params[:key])
    shapes = trip.shapes.order(:shape_pt_sequence).
             select(:shape_pt_lat, :shape_pt_lon)
    points = shapes.map { |s| [s.shape_pt_lat, s.shape_pt_lon] }

    render json: points
  end
end
