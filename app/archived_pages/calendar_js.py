# Alternate option to build calendar with javascript

from streamlit.components.v1 import html

'''
calendar_html = f"""
<!DOCTYPE html>
<html>
<head>
  <link href='https://cdn.jsdelivr.net/npm/fullcalendar@5.11.3/main.min.css' rel='stylesheet' />
  <script src='https://cdn.jsdelivr.net/npm/fullcalendar@5.11.3/main.min.js'></script>
  <style>
    {custom_css} <!-- custom CSS here -->
  </style>
</head>
<body>
  <div id='calendar'></div>
  <script>
    document.addEventListener('DOMContentLoaded', function() {{
      var calendarEl = document.getElementById('calendar');
      var calendar = new FullCalendar.Calendar(calendarEl, {{
        themeSystem: 'standard',
        initialView: 'dayGridMonth',
        dayMaxEventsRows: true,
        handleWindowResize: true,  // Ensures calendar resizes on window resize
        headerToolbar: {{
          left: 'today prev,next',
          center: 'title',
          right: 'timeGridDay,listWeek,dayGridMonth'
        }},
        buttonText: {{
          today: "Today",
          dayGridMonth: "Month",  // Customize the text for the month view button
          listWeek: "Week",  // Customize the text for the week view button
          timeGridDay: "Day"  // Customize the text for the list view button
        }},
        events: {calendar_events},  // events are here
        eventClick: function(info) {{
          alert('Event: ' + info.event.title);
        }}
      }});
      calendar.render();
    }});
  </script>
</body>
</html>
"""

# render the calendar with html
#html(calendar_html, height=800, width=1000, scrolling=True)
'''