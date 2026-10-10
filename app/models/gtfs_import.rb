require "csv"
require "zip"

# Imports the parts of a GTFS feed (https://gtfs.org/documentation/schedule/reference/)
# that cruzalinhas uses: the routes, their trips and the shapes those trips follow.
class GtfsImport
  BATCH_SIZE = 5_000

  FILES = {
    "routes.txt" => [Route, %w(route_id route_short_name route_long_name)],
    "trips.txt"  => [Trip,  %w(trip_id route_id shape_id)],
    "shapes.txt" => [Shape, %w(shape_id shape_pt_lat shape_pt_lon shape_pt_sequence)]
  }

  def self.call(zip_path)
    Zip::File.open(zip_path) do |zip|
      ActiveRecord::Base.transaction do
        FILES.each do |filename, (model, columns)|
          import zip.read(filename), model, columns
        end
      end
    end
  end

  # GTFS files are UTF-8 CSVs with a header row and an optional BOM
  def self.import(data, model, columns)
    data = data.force_encoding(Encoding::UTF_8).delete_prefix("﻿")
    CSV.new(data, headers: true, header_converters: ->(h) { h.strip }).each_slice(BATCH_SIZE) do |rows|
      model.insert_all rows.map { |row| columns.index_with { |column| row[column].presence } }
    end
  end
end
