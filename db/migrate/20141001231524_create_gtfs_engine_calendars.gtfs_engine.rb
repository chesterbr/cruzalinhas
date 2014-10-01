# This migration comes from gtfs_engine (originally 20140320045232)
class CreateGtfsEngineCalendars < ActiveRecord::Migration
  TABLE = :gtfs_engine_calendars

  def change
    create_table TABLE do |t|
      t.string  :service_id, null: false
      t.boolean :monday,     null: false
      t.boolean :tuesday,    null: false
      t.boolean :wednesday,  null: false
      t.boolean :thursday,   null: false
      t.boolean :friday,     null: false
      t.boolean :saturday,   null: false
      t.boolean :sunday,     null: false
      t.date    :start_date, null: false
      t.date    :end_date,   null: false

      t.references :data_set, null: false, index: true
    end

    add_index TABLE, :service_id
    add_index TABLE, :start_date
    add_index TABLE, :end_date
  end
end
