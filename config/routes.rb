Rails.application.routes.draw do
  # For details on the DSL available within this file, see http://guides.rubyonrails.org/routing.html
  get 'linhasquepassam' => 'python_api#linhasquepassam'
  get 'linha'           => 'python_api#linha'

  root 'home#index'
end
