function getResults() {
  var title = document.getElementById("job_title");
  var c_name = document.getElementById("company_name");
  var job_location = document.getElementById("job_location");
  var job_desciption = document.getElementById("job_description");
}

var server_data = [
  {"job_title": title},
  {"company_name": c_name},
  {"location": job_location},
  {"description": job_desciption},
];
console.log("Success getResults")

$.ajax({
  type: "POST",
  url: "{{ url_for('save_job') }}",
  data: JSON.stringify(server_data),
  contentType: "application/json",
  dataType: 'json' 
});
console.log("Success ajax")