# encoding: UTF-8
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

ActiveRecord::Schema.define(version: 20141001231536) do

  create_table "gtfs_engine_agencies", force: true do |t|
    t.string  "agency_id"
    t.string  "agency_name",     null: false
    t.string  "agency_url",      null: false
    t.string  "agency_timezone", null: false
    t.string  "agency_lang"
    t.string  "agency_fare_url"
    t.string  "agency_phone"
    t.integer "data_set_id",     null: false
  end

  add_index "gtfs_engine_agencies", ["agency_id"], name: "index_gtfs_engine_agencies_on_agency_id"
  add_index "gtfs_engine_agencies", ["data_set_id"], name: "index_gtfs_engine_agencies_on_data_set_id"

  create_table "gtfs_engine_calendar_dates", force: true do |t|
    t.string  "service_id",     null: false
    t.date    "date",           null: false
    t.integer "exception_type", null: false
    t.integer "data_set_id",    null: false
  end

  add_index "gtfs_engine_calendar_dates", ["data_set_id"], name: "index_gtfs_engine_calendar_dates_on_data_set_id"
  add_index "gtfs_engine_calendar_dates", ["date"], name: "index_gtfs_engine_calendar_dates_on_date"
  add_index "gtfs_engine_calendar_dates", ["service_id"], name: "index_gtfs_engine_calendar_dates_on_service_id"

  create_table "gtfs_engine_calendars", force: true do |t|
    t.string  "service_id",  null: false
    t.boolean "monday",      null: false
    t.boolean "tuesday",     null: false
    t.boolean "wednesday",   null: false
    t.boolean "thursday",    null: false
    t.boolean "friday",      null: false
    t.boolean "saturday",    null: false
    t.boolean "sunday",      null: false
    t.date    "start_date",  null: false
    t.date    "end_date",    null: false
    t.integer "data_set_id", null: false
  end

  add_index "gtfs_engine_calendars", ["data_set_id"], name: "index_gtfs_engine_calendars_on_data_set_id"
  add_index "gtfs_engine_calendars", ["end_date"], name: "index_gtfs_engine_calendars_on_end_date"
  add_index "gtfs_engine_calendars", ["service_id"], name: "index_gtfs_engine_calendars_on_service_id"
  add_index "gtfs_engine_calendars", ["start_date"], name: "index_gtfs_engine_calendars_on_start_date"

  create_table "gtfs_engine_data_sets", force: true do |t|
    t.string   "name",       null: false
    t.string   "title",      null: false
    t.string   "url",        null: false
    t.string   "etag",       null: false
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  add_index "gtfs_engine_data_sets", ["name"], name: "index_gtfs_engine_data_sets_on_name"
  add_index "gtfs_engine_data_sets", ["url"], name: "index_gtfs_engine_data_sets_on_url"

  create_table "gtfs_engine_fare_attributes", force: true do |t|
    t.string  "fare_id",           null: false
    t.float   "price",             null: false
    t.string  "currency_type",     null: false
    t.integer "payment_method",    null: false
    t.integer "transfers"
    t.integer "transfer_duration"
    t.integer "data_set_id",       null: false
  end

  add_index "gtfs_engine_fare_attributes", ["data_set_id"], name: "index_gtfs_engine_fare_attributes_on_data_set_id"
  add_index "gtfs_engine_fare_attributes", ["fare_id"], name: "index_gtfs_engine_fare_attributes_on_fare_id"

  create_table "gtfs_engine_fare_rules", force: true do |t|
    t.string  "fare_id",        null: false
    t.string  "route_id"
    t.string  "origin_id"
    t.string  "destination_id"
    t.string  "contains_id"
    t.integer "data_set_id",    null: false
  end

  add_index "gtfs_engine_fare_rules", ["data_set_id"], name: "index_gtfs_engine_fare_rules_on_data_set_id"
  add_index "gtfs_engine_fare_rules", ["fare_id"], name: "index_gtfs_engine_fare_rules_on_fare_id"

  create_table "gtfs_engine_feed_infos", force: true do |t|
    t.string  "feed_publisher_name", null: false
    t.string  "feed_publisher_url",  null: false
    t.string  "feed_lang",           null: false
    t.date    "feed_start_date"
    t.date    "feed_end_date"
    t.string  "feed_version"
    t.integer "data_set_id",         null: false
  end

  add_index "gtfs_engine_feed_infos", ["data_set_id"], name: "index_gtfs_engine_feed_infos_on_data_set_id"

  create_table "gtfs_engine_frequencies", force: true do |t|
    t.string  "trip_id",      null: false
    t.integer "start_time",   null: false
    t.integer "end_time",     null: false
    t.integer "headway_secs", null: false
    t.boolean "exact_times"
    t.integer "data_set_id",  null: false
  end

  add_index "gtfs_engine_frequencies", ["data_set_id"], name: "index_gtfs_engine_frequencies_on_data_set_id"
  add_index "gtfs_engine_frequencies", ["trip_id"], name: "index_gtfs_engine_frequencies_on_trip_id"

  create_table "gtfs_engine_routes", force: true do |t|
    t.string  "route_id",         null: false
    t.string  "agency_id"
    t.string  "route_short_name", null: false
    t.string  "route_long_name",  null: false
    t.string  "route_desc"
    t.integer "route_type",       null: false
    t.integer "route_url"
    t.string  "route_color"
    t.string  "route_text_color"
    t.integer "data_set_id",      null: false
  end

  add_index "gtfs_engine_routes", ["data_set_id"], name: "index_gtfs_engine_routes_on_data_set_id"
  add_index "gtfs_engine_routes", ["route_id"], name: "index_gtfs_engine_routes_on_route_id"
  add_index "gtfs_engine_routes", ["route_short_name"], name: "index_gtfs_engine_routes_on_route_short_name"

  create_table "gtfs_engine_shapes", force: true do |t|
    t.string  "shape_id",            null: false
    t.float   "shape_pt_lat",        null: false
    t.float   "shape_pt_lon",        null: false
    t.integer "shape_pt_sequence",   null: false
    t.float   "shape_dist_traveled"
    t.integer "data_set_id",         null: false
  end

  add_index "gtfs_engine_shapes", ["data_set_id"], name: "index_gtfs_engine_shapes_on_data_set_id"
  add_index "gtfs_engine_shapes", ["shape_id"], name: "index_gtfs_engine_shapes_on_shape_id"
  add_index "gtfs_engine_shapes", ["shape_pt_lat"], name: "index_gtfs_engine_shapes_on_shape_pt_lat"
  add_index "gtfs_engine_shapes", ["shape_pt_lon"], name: "index_gtfs_engine_shapes_on_shape_pt_lon"
  add_index "gtfs_engine_shapes", ["shape_pt_sequence"], name: "index_gtfs_engine_shapes_on_shape_pt_sequence"

  create_table "gtfs_engine_stop_times", force: true do |t|
    t.string  "stop_id",             null: false
    t.string  "trip_id",             null: false
    t.string  "arrival_time",        null: false
    t.string  "departure_time",      null: false
    t.integer "stop_sequence",       null: false
    t.string  "stop_headsign"
    t.integer "pickup_type"
    t.integer "drop_off_type"
    t.float   "shape_dist_traveled"
    t.integer "data_set_id",         null: false
  end

  add_index "gtfs_engine_stop_times", ["arrival_time"], name: "index_gtfs_engine_stop_times_on_arrival_time"
  add_index "gtfs_engine_stop_times", ["data_set_id"], name: "index_gtfs_engine_stop_times_on_data_set_id"
  add_index "gtfs_engine_stop_times", ["departure_time"], name: "index_gtfs_engine_stop_times_on_departure_time"
  add_index "gtfs_engine_stop_times", ["stop_id"], name: "index_gtfs_engine_stop_times_on_stop_id"
  add_index "gtfs_engine_stop_times", ["trip_id"], name: "index_gtfs_engine_stop_times_on_trip_id"

  create_table "gtfs_engine_stops", force: true do |t|
    t.string  "stop_id",             null: false
    t.string  "stop_code"
    t.string  "stop_name",           null: false
    t.string  "stop_desc"
    t.float   "stop_lat",            null: false
    t.float   "stop_lon",            null: false
    t.string  "zone_id"
    t.string  "stop_url"
    t.integer "location_type"
    t.integer "parent_station"
    t.string  "stop_timezone"
    t.integer "wheelchair_boarding"
    t.integer "data_set_id",         null: false
  end

  add_index "gtfs_engine_stops", ["data_set_id"], name: "index_gtfs_engine_stops_on_data_set_id"
  add_index "gtfs_engine_stops", ["stop_code"], name: "index_gtfs_engine_stops_on_stop_code"
  add_index "gtfs_engine_stops", ["stop_id"], name: "index_gtfs_engine_stops_on_stop_id"
  add_index "gtfs_engine_stops", ["stop_lat"], name: "index_gtfs_engine_stops_on_stop_lat"
  add_index "gtfs_engine_stops", ["stop_lon"], name: "index_gtfs_engine_stops_on_stop_lon"
  add_index "gtfs_engine_stops", ["zone_id"], name: "index_gtfs_engine_stops_on_zone_id"

  create_table "gtfs_engine_transfers", force: true do |t|
    t.string  "from_stop_id",      null: false
    t.string  "to_stop_id",        null: false
    t.integer "transfer_type",     null: false
    t.integer "min_transfer_time"
    t.integer "data_set_id",       null: false
  end

  add_index "gtfs_engine_transfers", ["data_set_id"], name: "index_gtfs_engine_transfers_on_data_set_id"
  add_index "gtfs_engine_transfers", ["from_stop_id"], name: "index_gtfs_engine_transfers_on_from_stop_id"
  add_index "gtfs_engine_transfers", ["to_stop_id"], name: "index_gtfs_engine_transfers_on_to_stop_id"

  create_table "gtfs_engine_trips", force: true do |t|
    t.string  "trip_id",               null: false
    t.string  "service_id",            null: false
    t.string  "trip_headsign"
    t.string  "trip_short_name"
    t.integer "direction_id"
    t.string  "block_id"
    t.string  "route_id",              null: false
    t.string  "shape_id"
    t.integer "wheelchair_accessible"
    t.integer "bikes_allowed"
    t.integer "data_set_id",           null: false
  end

  add_index "gtfs_engine_trips", ["block_id"], name: "index_gtfs_engine_trips_on_block_id"
  add_index "gtfs_engine_trips", ["data_set_id"], name: "index_gtfs_engine_trips_on_data_set_id"
  add_index "gtfs_engine_trips", ["route_id"], name: "index_gtfs_engine_trips_on_route_id"
  add_index "gtfs_engine_trips", ["service_id"], name: "index_gtfs_engine_trips_on_service_id"
  add_index "gtfs_engine_trips", ["shape_id"], name: "index_gtfs_engine_trips_on_shape_id"
  add_index "gtfs_engine_trips", ["trip_id"], name: "index_gtfs_engine_trips_on_trip_id"

end
