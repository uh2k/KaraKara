<%inherit file="_base.mako"/>


<%def name="title()">${data['title']}</%def>

<h1>${data['title']}</h1>

<div data-role="collapsible" data-content-theme="c">
    <h3>Queue Track</h3>
    <form action='/queue' method='POST' data-ajax="false">
        <input type='hidden' name='format'         value='redirect'      />
        <input type='text'   name='performer_name' value=''              placeholder='Enter your name' required />
        <input type='hidden' name='track_id'       value='${data['id']}' />
        <input type='submit' name='submit_'        value='Queue Track'   />
    </form>
</div>

<%
    def previews(track):
        previews = [attachment for attachment in track['attachments'] if attachment['type']=='preview']
        previews = [(preview, h.media_url(preview['location'])) for preview in previews]
        return previews
%>

<!-- html5 video -->
## class="hide_if_no_html5_video"
<div class="html5_video_embed" style="display: none;">
    <video class="video_placeholder" poster="${h.thumbnail_location_from_track(data)}" durationHint="${data['duration']}" controls>
        % for preview, url in previews(data):
            <source src="${url}" type="video/${h.video_mime_type(preview)}" />
            ##<p>${preview['extra_fields'].get('vcodec','unknown')}</p>
        % endfor
        <%doc>
            ##% for extension, video_type in h.video_files:
                ##% if extension in attachment['location']:
                ##% endif
            ##% endfor
        </%doc>
    </video>
</div>

<!-- video link & thumbnail carousel -->
## class="hide_if_html5_video"
<div class="html5_video_link">
    <!-- thumbnails -->
    <div class="thumbnails">
    % for thumbnail_url in h.attachment_locations_by_type(data,'thumbnail'):
        <img src="${thumbnail_url}" class="video_placeholder" style="display: none;"/>
    % endfor
    </div>
    
    ## Cycle the images as a carousel (custom carousel via plain hide/show)
    <script type="text/javascript">
        var current_thumbnail;
        cycleThumbnail();
        function cycleThumbnail() {
            
            if (current_thumbnail) {
                current_thumbnail.hide();
                current_thumbnail = current_thumbnail.next();
            }
            if (current_thumbnail==null || current_thumbnail.length==0) {
                current_thumbnail = $('.thumbnails').children('img:first');
            }
            if (current_thumbnail) {
                current_thumbnail.show();
            }
        }

        ## AllanC - currently the only form of video being generated by the mediaprocess is h264. In the future this could be changed to use the plain css selectors, for now this is sufficent.
        $(function() {
            if (Modernizr.video.h264 && !isWebOS()) { //HACK for isWebOS, webos incorrectly responds with 'probably'
                $('.html5_video_embed').show(); // Show html5 video element
                $('.html5_video_link' ).hide(); // Hide the static video link
            }
            else {
                interval_id = setInterval(cycleThumbnail, 3000); // Star the coursel for the staic images
            }
        });
    </script>
    

    % for preview, url in previews(data):
    <a href="${url}" data-role="button" rel=external target="_blank">Preview Video</a>
    ## ${preview['extra_fields'].get('target','unknown')}
    % endfor
</div>



<!-- details -->
<p>${data['description']}</p>


<!-- lyrics -->
<h2>Lyrics</h2>
% for lyrics in data['lyrics']:
    ##${lyrics['language']}
    % for line in lyrics['content'].split('\n'):
        <p>${line}</p>
    % endfor
% endfor
