require 'gtfs_engine/agency'
require 'gtfs_engine/calendar'
require 'gtfs_engine/calendar_date'
require 'gtfs_engine/data_set'
require 'gtfs_engine/fare_attribute'
require 'gtfs_engine/fare_rule'
require 'gtfs_engine/feed_info'
require 'gtfs_engine/frequency'
require 'gtfs_engine/route'
require 'gtfs_engine/shape'
require 'gtfs_engine/stop'
require 'gtfs_engine/stop_time'
require 'gtfs_engine/transfer'
require 'gtfs_engine/trip'

GtfsEngine.sources do |source|
  source.sptrans do
    title 'SPTrans'
    url '/tmp/gtfs-sptrans.zip'
  end
end
