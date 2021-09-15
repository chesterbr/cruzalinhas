class TripGeohash < ActiveRecord::Base
  belongs_to :trip, class_name: "GtfsEngine::Trip"

  def sptrans_url
    SptransUrl.find_by(sigla: trip.route_id)&.url
  end
end
