function getResults() {
  var title = document.getElementsByClassName("job_title");
  var c_name = document.getElementsByClassName("company_name");
  var job_location = document.getElementsByClassName("job_location");
  var job_desciption = document.getElementsByClassName("job_description");
}

var server_data = [
  {"job_title": title},
  {"company_name": c_name},
  {"location": job_location},
  {"description": job_desciption},
];

$.ajax({
  type: "POST",
  url: "{{ url_for('save_job') }}",
  data: JSON.stringify(server_data),
  contentType: "application/json",
  dataType: 'json' 
});