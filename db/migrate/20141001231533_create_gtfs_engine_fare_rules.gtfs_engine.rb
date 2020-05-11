# This migration comes from gtfs_engine (originally 20140406063500)
class CreateGtfsEngineFareRules < ActiveRecord::Migration[4.2]
  TABLE = :gtfs_engine_fare_rules

  def change
    create_table TABLE do |t|
      t.string :fare_id,        null: false
      t.string :route_id
      t.string :origin_id
      t.string :destination_id
      t.string :contains_id

      t.references :data_set, null: false, index: true
    end

    add_index TABLE, :fare_id
  end
end
