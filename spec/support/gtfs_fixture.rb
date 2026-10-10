module GtfsFixture
  # Zips spec/fixtures/gtfs/*.txt the way GTFS feeds are packaged (files at the root)
  def gtfs_fixture_zip
    path = Rails.root.join("tmp", "gtfs-fixture-#{Process.pid}.zip").to_s
    File.delete(path) if File.exist?(path)
    Zip::File.open(path, create: true) do |zip|
      Dir[Rails.root.join("spec/fixtures/gtfs/*.txt")].each do |file|
        zip.add(File.basename(file), file)
      end
    end
    path
  end
end

RSpec.configure { |config| config.include GtfsFixture }
