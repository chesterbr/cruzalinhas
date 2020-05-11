# This migration comes from gtfs_engine (originally 20140406073548)
class CreateGtfsEngineFeedInfos < ActiveRecord::Migration[4.2]
  TABLE = :gtfs_engine_feed_infos

  def change
    create_table TABLE do |t|
      t.string :feed_publisher_name, null: false
      t.string :feed_publisher_url,  null: false
      t.string :feed_lang,           null: false
      t.date   :feed_start_date
      t.date   :feed_end_date
      t.string :feed_version

      t.references :data_set, null: false, index: true
    end
  end
end
