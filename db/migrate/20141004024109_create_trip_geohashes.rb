class CreateTripGeohashes < ActiveRecord::Migration
  def change
    create_table :trip_geohashes do |t|
      t.references :trip, index: true
      t.string :geohash
    end
    add_index :trip_geohashes, [:geohash, :trip_id], unique: true
  end
end
