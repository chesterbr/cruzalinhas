# This migration comes from gtfs_engine (originally 20140320052005)
class CreateGtfsEngineStops < ActiveRecord::Migration
  TABLE = :gtfs_engine_stops

  def change
    create_table TABLE do |t|
      t.string  :stop_id,             null: false
      t.string  :stop_code
      t.string  :stop_name,           null: false
      t.string  :stop_desc
      t.float   :stop_lat,            null: false
      t.float   :stop_lon,            null: false
      t.string  :zone_id
      t.string  :stop_url
      t.integer :location_type
      t.integer :parent_station
      t.string  :stop_timezone
      t.integer :wheelchair_boarding

      t.references :data_set, null: false, index: true
    end

    add_index TABLE, :stop_id
    add_index TABLE, :stop_code
    add_index TABLE, :stop_lat
    add_index TABLE, :stop_lon
    add_index TABLE, :zone_id
  end
end
