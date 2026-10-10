# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# This file is the source Rails uses to define your schema when running `bin/rails
# db:schema:load`. When creating a new database, `bin/rails db:schema:load` tends to
# be faster and is potentially less error prone than running all of your
# migrations from scratch. Old migrations may fail to apply correctly if those
# migrations use external dependencies or application code.
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema[8.1].define(version: 2026_10_10_120000) do
  create_table "routes", force: :cascade do |t|
    t.string "route_id", null: false
    t.string "route_long_name"
    t.string "route_short_name"
    t.index ["route_id"], name: "index_routes_on_route_id", unique: true
  end

  create_table "shapes", force: :cascade do |t|
    t.string "shape_id", null: false
    t.float "shape_pt_lat", null: false
    t.float "shape_pt_lon", null: false
    t.integer "shape_pt_sequence", null: false
    t.index ["shape_id", "shape_pt_sequence"], name: "index_shapes_on_shape_id_and_shape_pt_sequence", unique: true
  end

  create_table "sptrans_urls", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.string "sigla"
    t.datetime "updated_at", null: false
    t.string "url"
    t.index ["sigla"], name: "index_sptrans_urls_on_sigla"
  end

  create_table "trip_geohashes", force: :cascade do |t|
    t.string "geohash"
    t.integer "trip_id"
    t.index ["geohash", "trip_id"], name: "index_trip_geohashes_on_geohash_and_trip_id", unique: true
    t.index ["trip_id"], name: "index_trip_geohashes_on_trip_id"
  end

  create_table "trips", force: :cascade do |t|
    t.string "route_id", null: false
    t.string "shape_id"
    t.string "trip_id", null: false
    t.index ["route_id"], name: "index_trips_on_route_id"
    t.index ["trip_id"], name: "index_trips_on_trip_id", unique: true
  end
end
