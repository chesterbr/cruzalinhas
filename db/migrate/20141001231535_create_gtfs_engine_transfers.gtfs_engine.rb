# This migration comes from gtfs_engine (originally 20140406072309)
class CreateGtfsEngineTransfers < ActiveRecord::Migration[4.2]
  TABLE = :gtfs_engine_transfers

  def change
    create_table TABLE do |t|
      t.string  :from_stop_id,      null: false
      t.string  :to_stop_id,        null: false
      t.integer :transfer_type,     null: false
      t.integer :min_transfer_time

      t.references :data_set, null: false, index: true
    end

    add_index TABLE, :from_stop_id
    add_index TABLE, :to_stop_id
  end
end
