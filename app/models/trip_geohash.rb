class TripGeohash < ActiveRecord::Base
  belongs_to :trip

  def sptrans_url
    SptransUrl.find_by(sigla: trip.route_id)&.url
  end
end
