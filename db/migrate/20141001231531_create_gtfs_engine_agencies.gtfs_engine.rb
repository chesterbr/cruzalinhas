# This migration comes from gtfs_engine (originally 20140401032609)
class CreateGtfsEngineAgencies < ActiveRecord::Migration[4.2]
  TABLE = :gtfs_engine_agencies

  def change
    create_table TABLE do |t|
      t.string :agency_id
      t.string :agency_name,     null: false
      t.string :agency_url,      null: false
      t.string :agency_timezone, null: false
      t.string :agency_lang
      t.string :agency_fare_url
      t.string :agency_phone

      t.references :data_set, null: false, index: true
    end

    add_index TABLE, :agency_id
  end
end
