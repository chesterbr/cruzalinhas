# This migration comes from gtfs_engine (originally 20140320050100)
class CreateGtfsEngineShapes < ActiveRecord::Migration[4.2]
  TABLE = :gtfs_engine_shapes

  def change
    create_table TABLE do |t|
      t.string  :shape_id,            null: false
      t.float   :shape_pt_lat,        null: false
      t.float   :shape_pt_lon,        null: false
      t.integer :shape_pt_sequence,   null: false
      t.float   :shape_dist_traveled

      t.references :data_set, null: false, index: true
    end

    add_index TABLE, :shape_id
    add_index TABLE, :shape_pt_sequence
    add_index TABLE, :shape_pt_lat
    add_index TABLE, :shape_pt_lon
  end
end
