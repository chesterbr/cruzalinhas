class CreateSptransUrls < ActiveRecord::Migration[6.1]
  def change
    create_table :sptrans_urls do |t|
      t.string :sigla
      t.string :url

      t.timestamps
    end
    add_index :sptrans_urls, :sigla
  end
end
