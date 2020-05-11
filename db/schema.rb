# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# Note that this schema.rb definition is the authoritative source for your
# database schema. If you need to create the application database on another
# system, you should be using db:schema:load, not running all the migrations
# from scratch. The latter is a flawed and unsustainable approach (the more migrations
# you'll amass, the slower it'll run and the greater likelihood for issues).
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema.define(version: 2014_10_04_024109) do

  create_table "gtfs_engine_agencies", force: :cascade do |t|
    t.string "agency_id"
    t.string "agency_name", null: false
    t.string "agency_url", null: false
    t.string "agency_timezone", null: false
    t.string "agency_lang"
    t.string "agency_fare_url"
    t.string "agency_phone"
    t.integer "data_set_id", null: false
    t.index ["agency_id"], name: "index_gtfs_engine_agencies_on_agency_id"
    t.index ["data_set_id"], name: "index_gtfs_engine_agencies_on_data_set_id"
  end

  create_table "gtfs_engine_calendar_dates", force: :cascade do |t|
    t.string "service_id", null: false
    t.date "date", null: false
    t.integer "exception_type", null: false
    t.integer "data_set_id", null: false
    t.index ["data_set_id"], name: "index_gtfs_engine_calendar_dates_on_data_set_id"
    t.index ["date"], name: "index_gtfs_engine_calendar_dates_on_date"
    t.index ["service_id"], name: "index_gtfs_engine_calendar_dates_on_service_id"
  end

  create_table "gtfs_engine_calendars", force: :cascade do |t|
    t.string "service_id", null: false
    t.boolean "monday", null: false
    t.boolean "tuesday", null: false
    t.boolean "wednesday", null: false
    t.boolean "thursday", null: false
    t.boolean "friday", null: false
    t.boolean "saturday", null: false
    t.boolean "sunday", null: false
    t.date "start_date", null: false
    t.date "end_date", null: false
    t.integer "data_set_id", null: false
    t.index ["data_set_id"], name: "index_gtfs_engine_calendars_on_data_set_id"
    t.index ["end_date"], name: "index_gtfs_engine_calendars_on_end_date"
    t.index ["service_id"], name: "index_gtfs_engine_calendars_on_service_id"
    t.index ["start_date"], name: "index_gtfs_engine_calendars_on_start_date"
  end

  create_table "gtfs_engine_data_sets", force: :cascade do |t|
    t.string "name", null: false
    t.string "title", null: false
    t.string "url", null: false
    t.string "etag", null: false
    t.datetime "created_at"
    t.datetime "updated_at"
    t.index ["name"], name: "index_gtfs_engine_data_sets_on_name"
    t.index ["url"], name: "index_gtfs_engine_data_sets_on_url"
  end

  create_table "gtfs_engine_fare_attributes", force: :cascade do |t|
    t.string "fare_id", null: false
    t.float "price", null: false
    t.string "currency_type", null: false
    t.integer "payment_method", null: false
    t.integer "transfers"
    t.integer "transfer_duration"
    t.integer "data_set_id", null: false
    t.index ["data_set_id"], name: "index_gtfs_engine_fare_attributes_on_data_set_id"
    t.index ["fare_id"], name: "index_gtfs_engine_fare_attributes_on_fare_id"
  end

  create_table "gtfs_engine_fare_rules", force: :cascade do |t|
    t.string "fare_id", null: false
    t.string "route_id"
    t.string "origin_id"
    t.string "destination_id"
    t.string "contains_id"
    t.integer "data_set_id", null: false
    t.index ["data_set_id"], name: "index_gtfs_engine_fare_rules_on_data_set_id"
    t.index ["fare_id"], name: "index_gtfs_engine_fare_rules_on_fare_id"
  end

  create_table "gtfs_engine_feed_infos", force: :cascade do |t|
    t.string "feed_publisher_name", null: false
    t.string "feed_publisher_url", null: false
    t.string "feed_lang", null: false
    t.date "feed_start_date"
    t.date "feed_end_date"
    t.string "feed_version"
    t.integer "data_set_id", null: false
    t.index ["data_set_id"], name: "index_gtfs_engine_feed_infos_on_data_set_id"
  end

  create_table "gtfs_engine_frequencies", force: :cascade do |t|
    t.string "trip_id", null: false
    t.integer "start_time", null: false
    t.integer "end_time", null: false
    t.integer "headway_secs", null: false
    t.boolean "exact_times"
    t.integer "data_set_id", null: false
    t.index ["data_set_id"], name: "index_gtfs_engine_frequencies_on_data_set_id"
    t.index ["trip_id"], name: "index_gtfs_engine_frequencies_on_trip_id"
  end

  create_table "gtfs_engine_routes", force: :cascade do |t|
    t.string "route_id", null: false
    t.string "agency_id"
    t.string "route_short_name", null: false
    t.string "route_long_name", null: false
    t.string "route_desc"
    t.integer "route_type", null: false
    t.integer "route_url"
    t.string "route_color"
    t.string "route_text_color"
    t.integer "data_set_id", null: false
    t.index ["data_set_id"], name: "index_gtfs_engine_routes_on_data_set_id"
    t.index ["route_id"], name: "index_gtfs_engine_routes_on_route_id"
    t.index ["route_short_name"], name: "index_gtfs_engine_routes_on_route_short_name"
  end

  create_table "gtfs_engine_shapes", force: :cascade do |t|
    t.string "shape_id", null: false
    t.float "shape_pt_lat", null: false
    t.float "shape_pt_lon", null: false
    t.integer "shape_pt_sequence", null: false
    t.float "shape_dist_traveled"
    t.integer "data_set_id", null: false
    t.index ["data_set_id"], name: "index_gtfs_engine_shapes_on_data_set_id"
    t.index ["shape_id"], name: "index_gtfs_engine_shapes_on_shape_id"
    t.index ["shape_pt_lat"], name: "index_gtfs_engine_shapes_on_shape_pt_lat"
    t.index ["shape_pt_lon"], name: "index_gtfs_engine_shapes_on_shape_pt_lon"
    t.index ["shape_pt_sequence"], name: "index_gtfs_engine_shapes_on_shape_pt_sequence"
  end

  create_table "gtfs_engine_stop_times", force: :cascade do |t|
    t.string "stop_id", null: false
    t.string "trip_id", null: false
    t.string "arrival_time", null: false
    t.string "departure_time", null: false
    t.integer "stop_sequence", null: false
    t.string "stop_headsign"
    t.integer "pickup_type"
    t.integer "drop_off_type"
    t.float "shape_dist_traveled"
    t.integer "data_set_id", null: false
    t.index ["arrival_time"], name: "index_gtfs_engine_stop_times_on_arrival_time"
    t.index ["data_set_id"], name: "index_gtfs_engine_stop_times_on_data_set_id"
    t.index ["departure_time"], name: "index_gtfs_engine_stop_times_on_departure_time"
    t.index ["stop_id"], name: "index_gtfs_engine_stop_times_on_stop_id"
    t.index ["trip_id"], name: "index_gtfs_engine_stop_times_on_trip_id"
  end

  create_table "gtfs_engine_stops", force: :cascade do |t|
    t.string "stop_id", null: false
    t.string "stop_code"
    t.string "stop_name", null: false
    t.string "stop_desc"
    t.float "stop_lat", null: false
    t.float "stop_lon", null: false
    t.string "zone_id"
    t.string "stop_url"
    t.integer "location_type"
    t.integer "parent_station"
    t.string "stop_timezone"
    t.integer "wheelchair_boarding"
    t.integer "data_set_id", null: false
    t.index ["data_set_id"], name: "index_gtfs_engine_stops_on_data_set_id"
    t.index ["stop_code"], name: "index_gtfs_engine_stops_on_stop_code"
    t.index ["stop_id"], name: "index_gtfs_engine_stops_on_stop_id"
    t.index ["stop_lat"], name: "index_gtfs_engine_stops_on_stop_lat"
    t.index ["stop_lon"], name: "index_gtfs_engine_stops_on_stop_lon"
    t.index ["zone_id"], name: "index_gtfs_engine_stops_on_zone_id"
  end

  create_table "gtfs_engine_transfers", force: :cascade do |t|
    t.string "from_stop_id", null: false
    t.string "to_stop_id", null: false
    t.integer "transfer_type", null: false
    t.integer "min_transfer_time"
    t.integer "data_set_id", null: false
    t.index ["data_set_id"], name: "index_gtfs_engine_transfers_on_data_set_id"
    t.index ["from_stop_id"], name: "index_gtfs_engine_transfers_on_from_stop_id"
    t.index ["to_stop_id"], name: "index_gtfs_engine_transfers_on_to_stop_id"
  end

  create_table "gtfs_engine_trips", force: :cascade do |t|
    t.string "trip_id", null: false
    t.string "service_id", null: false
    t.string "trip_headsign"
    t.string "trip_short_name"
    t.integer "direction_id"
    t.string "block_id"
    t.string "route_id", null: false
    t.string "shape_id"
    t.integer "wheelchair_accessible"
    t.integer "bikes_allowed"
    t.integer "data_set_id", null: false
    t.index ["block_id"], name: "index_gtfs_engine_trips_on_block_id"
    t.index ["data_set_id"], name: "index_gtfs_engine_trips_on_data_set_id"
    t.index ["route_id"], name: "index_gtfs_engine_trips_on_route_id"
    t.index ["service_id"], name: "index_gtfs_engine_trips_on_service_id"
    t.index ["shape_id"], name: "index_gtfs_engine_trips_on_shape_id"
    t.index ["trip_id"], name: "index_gtfs_engine_trips_on_trip_id"
  end

  create_table "trip_geohashes", force: :cascade do |t|
    t.integer "trip_id"
    t.string "geohash"
    t.index ["geohash", "trip_id"], name: "index_trip_geohashes_on_geohash_and_trip_id", unique: true
    t.index ["trip_id"], name: "index_trip_geohashes_on_trip_id"
  end

end
