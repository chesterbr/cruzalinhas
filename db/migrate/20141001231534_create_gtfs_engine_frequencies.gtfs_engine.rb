# This migration comes from gtfs_engine (originally 20140406071922)
class CreateGtfsEngineFrequencies < ActiveRecord::Migration
  TABLE = :gtfs_engine_frequencies

  def change
    create_table TABLE do |t|
      t.string  :trip_id,      null: false
      t.integer :start_time,   null: false
      t.integer :end_time,     null: false
      t.integer :headway_secs, null: false
      t.boolean :exact_times

      t.references :data_set, null: false, index: true
    end

    add_index TABLE, :trip_id
  end
end
