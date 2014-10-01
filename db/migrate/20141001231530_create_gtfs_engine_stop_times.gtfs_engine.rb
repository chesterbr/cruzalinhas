# This migration comes from gtfs_engine (originally 20140320052907)
class CreateGtfsEngineStopTimes < ActiveRecord::Migration
  TABLE = :gtfs_engine_stop_times

  def change
    create_table TABLE do |t|
      t.string  :stop_id,             null: false
      t.string  :trip_id,             null: false
      t.string  :arrival_time,        null: false
      t.string  :departure_time,      null: false
      t.integer :stop_sequence,       null: false
      t.string  :stop_headsign
      t.integer :pickup_type
      t.integer :drop_off_type
      t.float   :shape_dist_traveled

      t.references :data_set, null: false, index: true
    end

    add_index TABLE, :stop_id
    add_index TABLE, :trip_id
    add_index TABLE, :arrival_time
    add_index TABLE, :departure_time
  end
end
