# This migration comes from gtfs_engine (originally 20140320052508)
class CreateGtfsEngineTrips < ActiveRecord::Migration[4.2]
  TABLE = :gtfs_engine_trips

  def change
    create_table TABLE do |t|
      t.string  :trip_id,               null: false
      t.string  :service_id,            null: false
      t.string  :trip_headsign
      t.string  :trip_short_name
      t.integer :direction_id
      t.string  :block_id
      t.string  :route_id,              null: false
      t.string  :shape_id
      t.integer :wheelchair_accessible
      t.integer :bikes_allowed

      t.references :data_set, null: false, index: true
    end

    add_index TABLE, :trip_id
    add_index TABLE, :service_id
    add_index TABLE, :block_id
    add_index TABLE, :route_id
    add_index TABLE, :shape_id
  end
end
