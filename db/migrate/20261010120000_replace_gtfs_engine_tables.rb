class ReplaceGtfsEngineTables < ActiveRecord::Migration[8.1]
  GTFS_ENGINE_TABLES = %w(
    agencies calendar_dates calendars data_sets fare_attributes fare_rules
    feed_infos frequencies routes shapes stop_times stops transfers trips
  ).map { |name| "gtfs_engine_#{name}" }

  def up
    GTFS_ENGINE_TABLES.each { |table| drop_table table, if_exists: true }

    create_table :routes do |t|
      t.string :route_id, null: false
      t.string :route_short_name
      t.string :route_long_name
      t.index :route_id, unique: true
    end

    create_table :trips do |t|
      t.string :trip_id, null: false
      t.string :route_id, null: false
      t.string :shape_id
      t.index :trip_id, unique: true
      t.index :route_id
    end

    create_table :shapes do |t|
      t.string :shape_id, null: false
      t.float :shape_pt_lat, null: false
      t.float :shape_pt_lon, null: false
      t.integer :shape_pt_sequence, null: false
      t.index [:shape_id, :shape_pt_sequence], unique: true
    end
  end

  def down
    raise ActiveRecord::IrreversibleMigration
  end
end
