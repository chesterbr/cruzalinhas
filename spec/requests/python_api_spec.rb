require 'rails_helper'

RSpec.describe "Python API", type: :request do
  before do
    GtfsImport.call(gtfs_fixture_zip)
    TripGeohash.create!(trip: trip, geohash: "6gydxq")
    SptransUrl.create!(sigla: "1012-10", url: "https://sptrans.com.br/itinerarios/linha/?cdp=123")
  end

  let(:trip) { Trip.find_by(trip_id: "1012-10-0") }

  it "lists the lines that pass near a point" do
    get "/linhasquepassam.json", params: { lat: -23.432024, lng: -46.787121 }

    expect(response.parsed_body).to eq [{
      "url" => "https://sptrans.com.br/itinerarios/linha/?cdp=123",
      "hashes" => ["6gydxq"],
      "key" => trip.id,
      "nome" => "1012-10: Term. Jd. Britania - Jd. Monte Belo"
    }]
  end

  it "returns the points of a line, in sequence" do
    get "/linha.json", params: { key: trip.id }

    expect(response.parsed_body).to eq [
      [-23.4321, -46.7872],
      [-23.432024, -46.787121],
      [-23.4322, -46.7873]
    ]
  end
end
