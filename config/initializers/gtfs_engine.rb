GtfsEngine.sources do |source|
  source.sptrans do
    title 'SPTrans'
    url ENV["GTFS_SPTRANS_ZIP_FILE"]
  end
end
