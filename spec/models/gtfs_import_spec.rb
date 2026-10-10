require 'rails_helper'

RSpec.describe GtfsImport do
  before { GtfsImport.call(gtfs_fixture_zip) }

  it "imports routes, skipping the BOM and the columns we don't use" do
    expect(Route.pluck(:route_id, :route_short_name, :route_long_name)).to eq [
      ["1012-10", "1012-10", "Term. Jd. Britania - Jd. Monte Belo"],
      ["CPTM L10", "CPTM L10", "Rio Grande da Serra - Brás"]
    ]
  end

  it "imports trips in file order, with blank shape_ids as nil" do
    expect(Trip.order(:id).pluck(:trip_id, :route_id, :shape_id)).to eq [
      ["1012-10-0", "1012-10", "85940"],
      ["1012-10-1", "1012-10", "85941"],
      ["CPTM L10-0", "CPTM L10", nil]
    ]
  end

  it "links trips to their route and shape points" do
    trip = Trip.find_by(trip_id: "1012-10-0")
    expect(trip.route.route_long_name).to eq "Term. Jd. Britania - Jd. Monte Belo"
    expect(trip.shapes.order(:shape_pt_sequence).pluck(:shape_pt_lat, :shape_pt_lon)).to eq [
      [-23.4321, -46.7872],
      [-23.432024, -46.787121],
      [-23.4322, -46.7873]
    ]
    expect(Route.find_by(route_id: "1012-10").trips.count).to eq 2
  end
end
