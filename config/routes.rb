Rails.application.routes.draw do
  # These paths existed on the original (python) API. This allows us to
  # keep backwards compatibility with the existing client and external
  # users, and can become a thin mapping when/if we rethink the API.
  get 'linhasquepassam' => 'python_api#linhasquepassam'
  get 'linha'           => 'python_api#linha'
end
