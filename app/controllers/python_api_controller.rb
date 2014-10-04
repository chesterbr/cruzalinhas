class PythonApiController < ApplicationController

  def linhasquepassam
    render json: [{"url"=>"http://200.99.150.170/PlanOperWeb/detalheLinha.asp?TpDiaID=0&CdPjOID=12967", "hashes"=>["6gyf5f", "6gyfn4", "6gyfn5", "6gyfn6", "6gyf49", "6gyf46", "6gyf47", "6gyfh7", "6gyfh4", "6gyf51", "6gyfju", "6gyf4j", "6gyf4k", "6gyfjs", "6gyf4d", "6gyf4b", "6gyfhg", "6gyfjg", "6gyfjh", "6gyf50", "6gyf53", "6gyfjk"], "key"=>1295, "nome"=>"METRÔ L3-0 CORINTHIANS - ITAQUERA/PALMEIRAS - BARRA FUNDA"}, {"url"=>"http://200.99.150.170/PlanOperWeb/detalheLinha.asp?TpDiaID=0&CdPjOID=59661", "hashes"=>["6gyf4f", "6gyf4g", "6gyf4d", "6gyccm", "6gycch", "6gycct", "6gyf49", "6gycfp", "6gyf42", "6gyf43", "6gyf40", "6gyccy"], "key"=>1296, "nome"=>"METRÔ L4-0 BUTANTA/LUZ"}]
  end

  def linha
    route  = GtfsEngine::Route.find(params[:key])
    trip   = route.trips.first
    shapes = trip.shapes.order(:shape_pt_sequence).
             select(:shape_pt_lat, :shape_pt_lon)
    points = shapes.map { |s| [s.shape_pt_lat, s.shape_pt_lon] }

    render json: points
  end

end
