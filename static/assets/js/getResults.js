function getResults(job_id) {
  var title = document.getElementById("job_title_"+job_id).innerHTML;
  var c_name = document.getElementById("company_name_"+job_id).innerHTML;
  var job_location = document.getElementById("job_location_"+job_id).innerHTML;
  var job_desciption = document.getElementById("job_description_"+job_id).innerHTML;
  var checked = document.getElementById("job_save_"+job_id).checked;
  console.log(checked);
  // console.log(title)
  // console.log(c_name)
  // console.log(job_location)
  // console.log(job_desciption)
  $.ajax({
    type: "POST",
    url: "saved_jobs",
    data: JSON.stringify({
       "job_title": title,
       "company_name": c_name,
       "location": job_location,
       "description": job_desciption,
       "checked":checked
    }),
    contentType: "application/json",
    dataType: 'json'
  });
}