# This migration comes from gtfs_engine (originally 20140405235947)
class CreateGtfsEngineFareAttributes < ActiveRecord::Migration[4.2]
  TABLE = :gtfs_engine_fare_attributes

  def change
    create_table TABLE do |t|
      t.string  :fare_id,           null: false
      t.float   :price,             null: false
      t.string  :currency_type,     null: false
      t.integer :payment_method,    null: false
      t.integer :transfers
      t.integer :transfer_duration

      t.references :data_set, null: false, index: true
    end

    add_index TABLE, :fare_id
  end
end
