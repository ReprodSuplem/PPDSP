# PPDSP
A Case Study of the Profit-Maximizing Multi-Vehicle Pickup and Delivery Selection Problem for the Road Networks with the Integratable Nodes

This repository contains algorithms that reproduce the comparative experiments in our submission.

## Usage

- Run the script **csvio.py** to randomly generate the `csv` files corresponding to the parameters of the instances, which includes *requested information*, *vehicle information*, and *adjacency matrix* of the edges in the road network.
- Run the script **genIns.sh** to generate the `lp` files corresponding to all instances based on the above `csv` files and the prepared `tsp` benchmark samples.
- Use the MIP optimizer CPLEX to solve the generated `lp` files.

## Citation

If you want to cite these algorithms, please cite the preprint(https://doi.org/10.48550/arXiv.2208.14866) introducing them at arXiv:
```
@misc{arxiv/ZhaCIN22,
  author = {Zha, Aolong and Chang, Qiong and Imura, Naoto and Nishinari, Katsuhiro},
  title = {A Case Study of the Profit-Maximizing Multi-Vehicle Pickup and Delivery Selection Problem for the Road Networks with the Integratable Nodes},
  publisher = {arXiv},
  year = {2022},
  copyright = {Creative Commons Attribution 4.0 International},
  doi = {10.48550/arXiv.2208.14866},
}
```

