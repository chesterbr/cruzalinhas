class Route < ActiveRecord::Base
  has_many :trips, primary_key: :route_id, foreign_key: :route_id
end
