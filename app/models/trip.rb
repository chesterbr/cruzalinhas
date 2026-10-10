class Trip < ActiveRecord::Base
  belongs_to :route, primary_key: :route_id, foreign_key: :route_id
  has_many :shapes, primary_key: :shape_id, foreign_key: :shape_id
end
