const ctx = document.getElementById('grafico1');
      
new Chart(ctx, {
  type: 'pie',
  data: {
    labels: ['Acertos', 'Erros'],
    datasets: [{
      label: 'Qtd',
      data: [10, 5],
      borderWidth: 1
    }]
  },
  
});