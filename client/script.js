const query = (id) => `
{
  course(id: "${id}"){
    id
    courseName
    prerequisites {
      id
    }
  }
}
`
const options = (id) => { return {
    method: "post",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      query: query(id)
    })
  };
}

const loadData = async (id) => {
  const response = await fetch(`http://localhost:5000/graphql`, options(id))
  const data = await response.json()
  let buff = data['data']['course']['prerequisites'].slice(0)
  console.log("buff", buff)
  const results = [data['data']['course']]
  while (buff.length > 0) {
    
    const courseID = buff.pop()['id']
    const _response = await fetch(`http://localhost:5000/graphql`, options(courseID))
    const _data = await _response.json()
    if (!results.some(r => r['id'] === _data['data']['course']['id'])) {
      results.push(_data['data']['course'])
    }
    buff.push.apply(buff, _data['data']['course']['prerequisites'])
  }
  console.log("results", results)
  return results

}

const width = 400;
const height = 300;

const draw = async (id) => {
  d3.selectAll("svg > *").remove();

  const nodeRadius = 25;
  const svgNode = document.getElementById('root')
  svgNode.setAttribute("width", width)
  svgNode.setAttribute("height", height)
  svgNode.setAttribute("viewBox", `${-nodeRadius} ${-nodeRadius} ${width + 2 * nodeRadius} ${height + 2 * nodeRadius}`)
  const svgSelection = d3.select(svgNode);
  const defs = svgSelection.append('defs'); // For gradients
  
  // Use computed layout
  let data = await loadData(id)
  const strat = d3.dagStratify()
  strat.parentIds((d) => d.prerequisites.map(x => x.id))
  let dag = strat(data);

  const layout = d3.sugiyama()
    .size([width, height])
    .layering(d3.layeringSimplex())
    .decross(d3.decrossOpt())
    .coord(d3.coordVert())
  layout(dag)
  


  const steps = dag.size();
  const interp = d3.interpolateRainbow;
  const colorMap = {};
  dag.each((node, i) => {
    colorMap[node.id] = interp(i / steps);
  });
  
  // How to draw edges
  const line = d3.line()
    .curve(d3.curveCatmullRom)
    .x(d => d.x)
    .y(d => d.y);
    
  // Plot edges
  svgSelection.append('g')
    .selectAll('path')
    .data(dag.links())
    .enter()
    .append('path')
    .attr('d', ({ data }) => line(data.points))
    .attr('fill', 'none')
    .attr('stroke-width', 3)
    .attr('stroke', ({source, target}) => {
      const gradId = `${source.id}-${target.id}`;
      const grad = defs.append('linearGradient')
        .attr('id', gradId)
        .attr('gradientUnits', 'userSpaceOnUse')
        .attr('x1', source.x)
        .attr('x2', target.x)
        .attr('y1', source.y)
        .attr('y2', target.y);
      grad.append('stop').attr('offset', '0%').attr('stop-color', colorMap[source.id]);
      grad.append('stop').attr('offset', '100%').attr('stop-color', colorMap[target.id]);
      return `url(#${gradId})`;
    });
  
  // Select nodes
  const nodes = svgSelection.append('g')
    .selectAll('g')
    .data(dag.descendants())
    .enter()
    .append('g')
    .attr('transform', ({x, y}) => `translate(${x}, ${y})`);
  
  // Plot node circles
  nodes.append('circle')
    .attr('r', nodeRadius)
    .attr('fill', n => colorMap[n.id]);
  
  const arrow = d3.symbol().type(d3.symbolTriangle).size(nodeRadius * nodeRadius / 10.0);
  svgSelection.append('g')
    .selectAll('path')
    .data(dag.links())
    .enter()
    .append('path')
    .attr('d', arrow)
    .attr('transform', ({
      source,
      target,
      data
    }) => {
      const [end, start] = data.points.reverse();
      // This sets the arrows the node radius (20) + a little bit (3) away from the node center, on the last line segment of the edge. This means that edges that only span ine level will work perfectly, but if the edge bends, this will be a little off.
      const dx = start.x - end.x;
      const dy = start.y - end.y;
      const scale = nodeRadius * 1.15 / Math.sqrt(dx * dx + dy * dy);
      // This is the angle of the last line segment
      const angle = Math.atan2(-dy, -dx) * 180 / Math.PI + 90;
      console.log(angle, dx, dy);
      return `translate(${end.x + dx * scale}, ${end.y + dy * scale}) rotate(${angle})`;
    })
    .attr('fill', ({target}) => colorMap[target.id])
    .attr('stroke', 'white')
    .attr('stroke-width', 1.5);
  // Add text to nodes
  nodes.append('text')
    .attr('font-weight', 'bold')
    .attr('font-family', 'sans-serif')
    .attr('text-anchor', 'middle')
    .attr('alignment-baseline', 'middle')
    .attr('textLength', nodeRadius*2)
    .attr('fill', 'white')
    .append('tspan')
    .text(d => d.data.courseName.split(' ')[0])
    .attr('x', 0)
    .attr('y', 0)
    .append('tspan')
    .text(d => d.data.courseName.split(' ')[1])
    .attr('x', 0)
    .attr('dy', 15)

}
