# Compass configuration file

# Require any additional compass plugins here.

css_dir = "static"
sass_dir = "sass"
preferred_syntax = :sass
output_style = (environment == :production) ? :compressed : :expanded

on_stylesheet_saved do |filename|
   `python manage.py collectstatic --noinput`
end
