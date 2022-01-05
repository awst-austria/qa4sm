import {Component, Input, OnInit} from '@angular/core';
import {FilterModel} from '../basic-filter/filter-model';
import {TreeNode} from 'primeng/api';
import {IsmnNetworkService} from '../../../core/services/filter/ismn-network-service';
import {BehaviorSubject} from 'rxjs';
import {DatasetComponentSelectionModel} from '../../../dataset/components/dataset/dataset-component-selection-model';
import {IsmnNetworkDto} from '../../../core/services/filter/ismn-network.dto';


@Component({
  selector: 'qa-ismn-network-filter',
  templateUrl: './ismn-network-filter.component.html',
  styleUrls: ['./ismn-network-filter.component.scss']
})
export class IsmnNetworkFilterComponent implements OnInit {

  @Input() filterModel$: BehaviorSubject<FilterModel>;
  @Input() datasetModel: DatasetComponentSelectionModel;

  networkSelectorVisible = false;

  networkTree: TreeNode[];
  selectedNetworks: TreeNode[] = [];

  constructor(public networkService: IsmnNetworkService) {
  }

  ngOnInit(): void {
    this.initComponent();
    // in case the filter model gets updated externally we need to re-initialize this component
    this.filterModel$.subscribe(model => {
      if (model != null) {
        this.initComponent();
      }
    });
  }

  showNetworkSelector(): void {
    this.networkSelectorVisible = true;
  }


  private buildNetworkTree(networks: IsmnNetworkDto[], networksToBeSelected: string): void {
    this.networkTree = [];
    networks.forEach(net => {
      let continentFound = false;
      for (let i = 0; i < this.networkTree.length; i++) {
        if (net.continent === this.networkTree[i].key) {
          this.networkTree[i].children.push(this.networkDtoToTreeModel(net, this.networkTree[i]));
          continentFound = true;
        }
      }

      if (continentFound === false) {
        const newContinent: TreeNode = {key: net.continent, label: net.continent};
        newContinent.children = [];
        newContinent.children.push(this.networkDtoToTreeModel(net, newContinent));
        this.networkTree.push(newContinent);
      }
    });

    // do preselection
    this.selectedNetworks.length = 0;
    this.networkTree.forEach(continent => {
      continent.children.forEach(net => {
        if (networksToBeSelected.includes(net.key)) {
          continent.partialSelected = true;
          this.selectedNetworks.push(net);
        }
      });
    });
    //this.doNetworkPreselection(this.networkTree, networksToBeSelected);
  }

  private networkDtoToTreeModel(network: IsmnNetworkDto, parentNode: TreeNode): TreeNode<IsmnNetworkDto> {
    return {key: network.name, label: network.name, data: network, parent: parentNode};
  }

  public onNetworkUnselect(e): void {
    console.log('Unselect network: ' + e);
  }

  public onNetworkSelect(e): void {
    console.log('Network selected. Selection size: ' + this.selectedNetworks.length);
    // if (e.node.data == null) {  // Full continent selected
    //
    //   e.node.children.forEach(network => {
    //     console.log('Adding network: ' + network);
    //     console.log(network);
    //     this.addNetworkToFilterModel(network);
    //   });
    // } else { // Network selected
    //
    // }
    //
    // console.log('New paramter: ' + this.filterModel$.value.parameters);
  }

  private addNetworkToFilterModel(network: IsmnNetworkDto): void {
    const filter = this.filterModel$.value;
    if (!filter.parameters.includes(network.name)) {
      if (filter.parameters.length > 0) {
        filter.parameters = filter.parameters + ',';
      }
      filter.parameters = filter.parameters + network.name;
      this.filterModel$.next(filter);
    }
  }

  private removeNetworkFromFilterModel(network: IsmnNetworkDto): void {
    const filter = this.filterModel$.value;
    const posWithComa = filter.parameters.indexOf(',' + network.name);
    const pos = filter.parameters.indexOf(network.name);
    if (posWithComa > -1) {
      filter.parameters.replace(',' + network.name, '');
    } else if (pos > -1) {
      filter.parameters.replace(network.name, '');
    }
  }

  private initComponent(): void {
    this.loadNetworks();
  }

  private loadNetworks(): void {
    this.networkService.getNetworksByDatasetVersionId(this.datasetModel.selectedVersion.id).subscribe(data => {
      this.buildNetworkTree(data, this.filterModel$.value.filterDto.default_parameter);
    });
  }

  private doNetworkPreselection(treeNodes: TreeNode[], networksToBeSelected: string): void {
    this.selectedNetworks.length = 0;
    treeNodes.forEach(node => {
      if (networksToBeSelected.includes(node.label)) {
        this.selectedNetworks.push(node);
      }

      if (node.children !== undefined) {
        node.children.forEach(child => {
          //check child if the parent is not selected
          if (networksToBeSelected.includes(child.label) && !networksToBeSelected.includes(node.label)) {
            node.partialSelected = true;
            child.parent = node;
          }

        });
      } else {
        return;
      }

      this.doNetworkPreselection(node.children, networksToBeSelected);

      node.children.forEach(child => {
        if (child.partialSelected) {
          node.partialSelected = true;
        }
      });
    });
  }
}
