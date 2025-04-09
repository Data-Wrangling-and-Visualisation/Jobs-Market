<template>
  <div class="main-page">
  <h1 id="title">Job Listings Bubble Chart</h1>
  <div class="filter-container">
      <label for="location-select">Filter by Location:</label>
      <select id="location-select" @change="filterLocation($event)">
        <option value="">All Locations</option>
        <option v-for="job in uniqueLocations" :key="job" :value="job">{{ job }}</option>
      </select>
    </div>
  <div class="chart-container">
    <div ref="chart"></div>
  </div>

  </div>
</template>

<script>
import * as d3 from 'd3';

export default {
  name: 'BubbleChart',
  data() {
    return {
      // jobListings: [
      //   { job_title: 'Software Engineer', salary: 100000, vacancies: 15, location: 'New York', employment_type: 'Full-time', posting_date: '2025-04-07' },
      //   { job_title: 'Data Scientist', salary: 120000, vacancies: 8, location: 'San Francisco', employment_type: 'Full-time', posting_date: '2025-04-06' },
      //   { job_title: 'Product Manager', salary: 110000, vacancies: 10, location: 'Los Angeles', employment_type: 'Contract', posting_date: '2025-04-05' },
      //   { job_title: 'UX Designer', salary: 90000, vacancies: 20, location: 'Austin', employment_type: 'Full-time', posting_date: '2025-04-04' },
      //   { job_title: 'DevOps Engineer', salary: 95000, vacancies: 5, location: 'Chicago', employment_type: 'Part-time', posting_date: '2025-04-03' },
      //   { job_title: 'Backend Developer', salary: 105000, vacancies: 12, location: 'Seattle', employment_type: 'Full-time', posting_date: '2025-04-02' },
      //   { job_title: 'Frontend Developer', salary: 95000, vacancies: 18, location: 'Boston', employment_type: 'Full-time', posting_date: '2025-04-01' }
      // ],
      filteredJobs: null,
      jobListings: [],
    };
  },
  mounted() {
    fetch("http://localhost:5000/api/jobs")
      .then(res => res.json())
      .then(data => {
        this.jobListings = data.slice(0, 100);
        this.filteredJobs = data.slice(0, 100); // optional: initialize filtered list
        this.createChart();
      })
      .catch(err => {
        console.error("Failed to load jobs:", err);
      });
  },
  computed: {
  uniqueLocations() {
    return [...new Set(this.jobListings.map(d => d.location))];
  }
  },
  methods: {
    filterLocation(e) {
    const selected = e.target.value;
    this.filteredJobs = selected
      ? this.jobListings.filter(d => d.location === selected)
      : this.jobListings;
    this.createChart();
  },

    createChart() {
      d3.select(this.$refs.chart).selectAll('*').remove();
      const data = this.filteredJobs || this.jobListings;

  const colorScale = d3.scaleOrdinal()
  .domain([...new Set(data.map(d => d.location))]) // Unique locations
  .range(d3.schemeCategory10); // Or any other palette


  // Set width and height dynamically based on window size
  const width = window.innerWidth;
  const height = window.innerHeight;

  const svg = d3.select(this.$refs.chart)
    .append('svg')
    .attr('width', width)
    .attr('height', height);

  // Scale the bubble size based on number of vacancies
  const radiusScale = d3.scaleSqrt()
    .domain([0, d3.max(data, d => d.vacancies)])
    .range([0, 50]);

  // Simulation forces
  const simulation = d3.forceSimulation(data)
    .force('x', d3.forceX(width / 2).strength(0.05))  // Pulling bubbles to the center horizontally
    .force('y', d3.forceY(height / 2).strength(0.05)) // Pulling bubbles to the center vertically
    .force('collide', d3.forceCollide(d => radiusScale(d.vacancies) + 2)) // Reduce the radius to let them overlap slightly
    .on('tick', ticked);

  function wrap(d) {
  const text = d3.select(this);
  const words = d.job_title.split(/\s+/).reverse();
  const r = d.radius || 40; // fallback radius
  const width = r * 1.8;    // wrap width a bit less than diameter
  let word,
    line = [],
    lineNumber = 0,
    lineHeight = 1.1, // ems
    y = d.y,
    x = d.x,
    tspan = text.text(null).append("tspan").attr("x", x).attr("y", y).attr("dy", 0 + "em");

  while ((word = words.pop())) {
    line.push(word);
    tspan.text(line.join(" "));
    if (tspan.node().getComputedTextLength() > width) {
      line.pop();
      tspan.text(line.join(" "));
      line = [word];
      tspan = text
        .append("tspan")
        .attr("x", x)
        .attr("y", y)
        .attr("dy", ++lineNumber * lineHeight + "em")
        .text(word);
    }
  }
}
  // Create the bubbles
  const bubbles = svg.selectAll('circle')
    .data(data)
    .enter().append('circle')
    .attr('r', d => radiusScale(d.vacancies))
    .attr('fill', d => colorScale(d.location))
    .attr('stroke', 'black')
    .attr('stroke-width', 1)
    .on('mouseover', function(event, d) {
      d3.select(this).attr('fill', 'orange');
      // Tooltip with job info
      const tooltip = d3.select('body').append('div')
        .attr('class', 'tooltip')
        .html(`
          <strong>${d.job_title}</strong><br>
          Location: ${d.location}<br>
          Employment Type: ${d.employment_type}<br>
          Salary: $${d.salary}<br>
          Vacancies: ${d.vacancies}<br>
          Posted: ${d.posting_date}
        `)
        .style('position', 'absolute')
        .style('left', `${event.pageX + 10}px`)
        .style('top', `${event.pageY + 10}px`);
    })
    .on('mouseout', function() {
      d3.select(this).attr('fill', d => colorScale(d.location))
      d3.selectAll('.tooltip').remove();
    });

  // Add job titles and average salaries on top of the bubbles
  const labels = svg.selectAll('text')
  .data(data)
  .enter().append('text')
  .attr('text-anchor', 'middle')
  .attr('alignment-baseline', 'middle')
  .style('pointer-events', 'none')
  .style('fill', 'white')
  .style('font-family', 'Verdana, sans-serif')
  .style('font-size', d => {
    const r = radiusScale(d.vacancies);
    const maxFontSize = 14;
    const minFontSize = 6;
    const scale = Math.max(minFontSize, Math.min(maxFontSize, r / 2));
    return `${scale}px`;
  })
  .each(function(d) {
    d.radius = radiusScale(d.vacancies); // save for wrap()
  })
  .each(wrap);

  // Update position of bubbles on every tick of the simulation
  function ticked() {
    bubbles.attr('cx', d => d.x).attr('cy', d => d.y);

    labels.selectAll('tspan')
      .attr('x', d => d.x)
      .attr('y', d => d.y);
  }
  
  const legend = svg.append('g')
  .attr('class', 'legend')
  .attr('transform', 'translate(20, 20)');

const locations = colorScale.domain();

legend.selectAll('rect')
  .data(locations)
  .enter()
  .append('rect')
  .attr('x', 0)
  .attr('y', (d, i) => i * 25)
  .attr('width', 20)
  .attr('height', 20)
  .attr('fill', d => colorScale(d));

legend.selectAll('text')
  .data(locations)
  .enter()
  .append('text')
  .attr('x', 30)
  .attr('y', (d, i) => i * 25 + 15)
  .text(d => d)
  .style('font-size', '14px')
  .style('font-family', 'Verdana');


  
  
    }

  }
};
</script>

<style>

html, body {
  margin: 0px;
  padding: 0px;
  height: 100%;
  width: 100%;
  background-color: white; /*	#495057;*/  
}

#title {
  display: flex;
  justify-content: center; 
  align-items: center;     
}
.chart-container {
  display: flex;
  justify-content: center; 
  align-items: center;
}

.tooltip {
  background: #fff;
  border: 1px solid #ccc;
  padding: 10px;
  font-size: 14px;
  border-radius: 5px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.legend text {
  fill: #333;
}

.filter-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 20px 0;
  gap: 10px;
  font-family: 'Verdana', sans-serif;
  font-size: 16px;
}

.filter-container label {
  font-weight: bold;
}

.filter-container select {
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid #ccc;
  font-size: 16px;
  background-color: #f9f9f9;
  transition: border 0.3s, box-shadow 0.3s;
}

.filter-container select:focus {
  border-color: #4a90e2;
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.2);
  outline: none;
}


</style>

