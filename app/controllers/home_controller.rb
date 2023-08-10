class HomeController < ApplicationController
  def index
  end

  def version
    render html: Git.open(Rails.root).log.first.sha
  end
end
