class TripGeohash < ActiveRecord::Base
  belongs_to :trip, class_name: "GtfsEngine::Trip"

  def sptrans_url
    text_id = trip.route.route_short_name
    sanitized_id = CGI::escape(I18n.transliterate(text_id))

    "http://200.99.150.170/PlanOperWeb/linhaselecionada.asp?Linha=#{sanitized_id}"
  end
end
