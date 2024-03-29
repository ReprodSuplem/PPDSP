# PPDSP
A Case Study of the Profit-Maximizing Multi-Vehicle Pickup and Delivery Selection Problem for the Road Networks with the Integratable Nodes

This repository contains all source code that can reproduce the comparative experiments in our submission.

## Usage

- Run the script **csvio.py** to randomly generate the `csv` files corresponding to the parameters of the instances, which includes *requests information*, *vehicles information*, and *adjacency matrix of the edges in the road network*.
- Run the script **genIns.sh** to generate the `lp` files corresponding to all instances based on the above `csv` files and the prepared `tsp` benchmark samples.
- Use the MIP optimizer CPLEX to solve the generated `lp` files.

## Citation

If you want to cite this study, please cite the [preprint](https://doi.org/10.48550/arXiv.2208.14866) introducing them at arXiv:
```
@misc{arxiv/ZhaCIN22,
  author = {Zha, Aolong and Chang, Qiong and Imura, Naoto and Nishinari, Katsuhiro},
  title = {A case study of the profit-maximizing multi-vehicle pickup and delivery selection problem for the road networks with the integratable nodes},
  publisher = {arXiv},
  year = {2022},
  copyright = {Creative Commons Attribution 4.0 International},
  doi = {10.48550/arXiv.2208.14866},
}
```

