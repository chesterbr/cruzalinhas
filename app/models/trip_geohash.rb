class TripGeohash < ActiveRecord::Base
  belongs_to :trip, class_name: "GtfsEngine::Trip"
end
